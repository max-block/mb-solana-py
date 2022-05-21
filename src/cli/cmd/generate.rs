use crate::account::{generate_keypair, keypair_bytes_to_string};
use crate::cli::util::print_colored_json;
use solana_sdk::signer::Signer;
use std::collections::HashMap;

pub fn run(limit: u16, private_key_as_array: bool) {
    let mut result: HashMap<String, String> = HashMap::with_capacity(limit as usize);
    for _ in 0..limit {
        let k = generate_keypair();
        let private_key = if private_key_as_array { keypair_bytes_to_string(k.to_bytes()) } else { k.to_base58_string() };
        result.insert(k.pubkey().to_string(), private_key);
    }
    print_colored_json(&serde_json::to_string(&result).unwrap());
}
