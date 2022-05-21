use crate::account::{keypair_bytes_to_string, keypair_from_str};
use solana_sdk::signature::{read_keypair_file, Keypair, Signer};

pub fn run(private_key: String) {
    if let Some(keypair) = keypair_from_str(&private_key) {
        return print_keypair(keypair);
    }
    if let Ok(keypair) = read_keypair_file(private_key) {
        return print_keypair(keypair);
    }
    println!("invalid private key");
}

fn print_keypair(keypair: Keypair) {
    println!("public: {}", keypair.pubkey());
    println!("private base58: {}", keypair.to_base58_string());
    println!("private arr: {}", keypair_bytes_to_string(keypair.to_bytes()));
}
