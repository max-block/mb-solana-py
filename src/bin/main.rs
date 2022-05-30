use clap::{Command, CommandFactory, Parser, Subcommand};
use clap_complete::{generate, Generator, Shell};
use std::io;

use mb_solana::cli::cmd;

#[derive(Parser)]
struct Cli {
    #[clap(subcommand)]
    command: Commands,

    #[clap(long = "generate", arg_enum)]
    generator: Option<Shell>,
}

#[derive(Subcommand)]
enum Commands {
    Generate(GenerateCommand),
    KeypairFromPrivate(KeypairFromPrivateCommand),
    KeypairFromMnemonic(KeypairFromMnemonicCommand),
    Split,
}

/// Generate new keypair
#[derive(Parser)]
struct GenerateCommand {
    #[clap(long, default_value_t = 1)]
    limit: u16,
    #[clap(long)]
    array: bool,
}

#[derive(Parser)]
struct KeypairFromPrivateCommand {
    private_key: String,
}

/// Get m/44'/501'/0'/0' keypair from a mnemonic
#[derive(Parser)]
struct KeypairFromMnemonicCommand {
    #[clap(short='m')]
    mnemonic: Option<String>,
}

fn main() {
    let cli = Cli::parse();

    if let Some(generator) = cli.generator {
        let mut cmd = Cli::command();
        eprintln!("Generating completion file for {:?}...", generator);
        print_completions(generator, &mut cmd);
    } else {
        match cli.command {
            Commands::Generate(c) => cmd::generate::run(c.limit, c.array),
            Commands::KeypairFromPrivate(c) => cmd::keypair_from_private::run(c.private_key),
            Commands::KeypairFromMnemonic(c) => cmd::keypair_from_mnemonic::run(c.mnemonic),
            Commands::Split => cmd::split::run(),
        }
    }
}

fn print_completions<G: Generator>(gen: G, cmd: &mut Command) {
    generate(gen, cmd, cmd.get_name().to_string(), &mut io::stdout());
}
