use std::process;
use colored_json::ToColoredJson;
use solana_sdk::signature::{Keypair, Signer};
use crate::account::keypair_bytes_to_string;

pub fn print_colored_json(data: &str) {
    println!("{}", data.to_colored_json_auto().unwrap());
}

pub fn print_keypair(keypair: Keypair) {
    println!("public: {}", keypair.pubkey());
    println!("private base58: {}", keypair.to_base58_string());
    println!("private arr: {}", keypair_bytes_to_string(keypair.to_bytes()));
}

pub fn print_fatal(message: impl AsRef<str>) ->! {
    eprintln!("fatal error: {}", message.as_ref());
    process::exit(1);
}