use clap::{Parser, Subcommand};

use mb_solana::cli::cmd;

#[derive(Parser)]
struct Cli {
    #[clap(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Generate(GenerateCommand),
    Keypair(KeypairCommand),
    Split,
}

#[derive(Parser)]
struct GenerateCommand {
    #[clap(long, default_value_t = 1)]
    limit: u16,
    #[clap(long)]
    array: bool,
}

#[derive(Parser)]
struct KeypairCommand {
    private_key: String,
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Generate(c) => cmd::generate::run(c.limit, c.array),
        Commands::Keypair(c) => cmd::keypair::run(c.private_key),
        Commands::Split => cmd::split::run(),
    }
}
