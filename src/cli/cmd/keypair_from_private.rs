use crate::account::keypair_from_str;
use crate::cli::util::{print_fatal, print_keypair};
use solana_sdk::signature::read_keypair_file;

pub fn run(private_key: String) {
    if let Some(keypair) = keypair_from_str(&private_key) {
        return print_keypair(keypair);
    }
    if let Ok(keypair) = read_keypair_file(private_key) {
        return print_keypair(keypair);
    }
    print_fatal("invalid private key");
}
