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
    New(NewCommand),
    Private(PrivateCommand),
    Mnemonic(MnemonicCommand),
}

/// Generate new keypair
#[derive(Parser)]
struct NewCommand {
    #[clap(long, default_value_t = 1)]
    limit: u16,
    #[clap(long)]
    array: bool,
}

/// Get keypair from a private key
#[derive(Parser)]
struct PrivateCommand {
    #[clap(short = 'p')]
    private_key: Option<String>,
}

/// Get m/44'/501'/0'/0' keypair from a mnemonic
#[derive(Parser)]
struct MnemonicCommand {
    #[clap(short = 'm')]
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
            Commands::New(c) => cmd::new_cmd::run(c.limit, c.array),
            Commands::Private(c) => cmd::private_cmd::run(c.private_key),
            Commands::Mnemonic(c) => cmd::mnemonic_cmd::run(c.mnemonic),
        }
    }
}

fn print_completions<G: Generator>(gen: G, cmd: &mut Command) {
    generate(gen, cmd, cmd.get_name().to_string(), &mut io::stdout());
}
