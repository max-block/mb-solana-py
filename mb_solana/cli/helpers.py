import json
import os
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from json import JSONEncoder
from typing import Callable, TypeVar, Union

import click
import toml
import yaml
from click import Context
from jinja2 import Environment, Template, TemplateSyntaxError, meta
from pydantic import BaseModel, ValidationError, validator

_jinja_env = Environment(autoescape=True)


class BaseCmdConfig(BaseModel):
    @validator("*", pre=True)
    def env_template_validator(cls, v):
        return env_validator(v)

    class Config:
        extra = "forbid"


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, BaseModel):
            return o.dict()
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, Exception):
            return str(o)
        return JSONEncoder.default(self, o)


def env_validator(v):
    if isinstance(v, str):
        try:
            ast = _jinja_env.parse(v)
            envs = meta.find_undeclared_variables(ast)
            if envs:
                data = {}
                for env in envs:
                    if not os.getenv(env):
                        click.secho(f"can't get environment variable {env}", err=True, fg="red")
                        exit(1)
                    data[env] = os.getenv(env)
                template = Template(v)
                return template.render(data)
        except TemplateSyntaxError as err:
            click.secho(f"jinja syntax error: {str(err)}", err=True, fg="red")
            click.secho(v)
            exit(1)
    return v


ConfigImpl = TypeVar("ConfigImpl")  # the variable return type


def parse_config(ctx: Context, config_path: str, config_cls: Callable[..., ConfigImpl]) -> ConfigImpl:
    file_data = read_config_file_or_exit(config_path)
    try:
        if ctx.obj["nodes"]:
            if "nodes" in file_data:
                file_data["nodes"] = ctx.obj["nodes"]
            elif "node" in file_data:
                file_data["node"] = ctx.obj["nodes"][0]
        return config_cls(**file_data)

    except ValidationError as err:
        click.secho(str(err), err=True, fg="red")
        exit(1)


def read_config_file_or_exit(file_path: str) -> dict:
    try:
        with open(file_path) as f:
            if file_path.endswith(".toml"):
                return toml.load(f)  # type:ignore
            return yaml.full_load(f)
    except Exception as err:
        click.secho(f"can't parse config file: {str(err)}", fg="red")
        exit(1)


def print_config_and_exit(ctx: Context, config):
    if ctx.obj["config"]:
        print_json(config.dict())
        exit(0)


def print_json(obj: Union[dict, list, BaseModel]):
    click.echo(json.dumps(obj, indent=2, cls=CustomJSONEncoder))
