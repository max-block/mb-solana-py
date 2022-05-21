use bip39::Language::English;
use bip39::{Mnemonic, MnemonicType, Seed};
use itertools::Itertools;
use solana_sdk::bs58;
use solana_sdk::signature::{keypair_from_seed, Keypair, Signer};

pub fn generate_keypair() -> Keypair {
    let mnemonic = Mnemonic::new(MnemonicType::Words24, English);
    let seed = Seed::new(&mnemonic, &Keypair::new().pubkey().to_string());
    keypair_from_seed(seed.as_bytes()).unwrap()
}

pub fn keypair_bytes_to_string(keypair: [u8; 64]) -> String {
    let r = keypair.iter().map(|x| x.to_string()).join(",");
    format!("[{}]", r)
}

pub fn keypair_from_str(private_key: &str) -> Option<Keypair> {
    if private_key.starts_with('[') {
        match serde_json::from_str::<Vec<u8>>(private_key) {
            Ok(res) => Keypair::from_bytes(res.as_slice()).ok(),
            Err(_) => None,
        }
    } else {
        match bs58::decode(private_key).into_vec() {
            Ok(res) => Keypair::from_bytes(res.as_slice()).ok(),
            Err(_) => None,
        }
    }
}
