use bip39::Language::English;
use bip39::{Mnemonic, Seed};
use solana_sdk::derivation_path::DerivationPath;
use solana_sdk::signature::{keypair_from_seed_and_derivation_path};
use crate::cli::util::{print_fatal, print_keypair};

pub fn run(mnemonic: Option<String>) {
    let mnemonic = match mnemonic {
        Some(mnemonic) => mnemonic,
        None => rpassword::prompt_password("mnemonic:").unwrap()
    };


    let mnemonic = match Mnemonic::from_phrase(&mnemonic, English) {
        Ok(m) => m,
        Err(e) => print_fatal(e.to_string())
    };

    let seed = Seed::new(&mnemonic, "");
    let path = DerivationPath::new_bip44(Some(0), Some(0));
    let keypair = keypair_from_seed_and_derivation_path(seed.as_bytes(), Some(path)).unwrap();
    print_keypair(keypair);
}
