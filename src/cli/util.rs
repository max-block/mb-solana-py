use colored_json::ToColoredJson;

pub fn print_colored_json(data: &str) {
    println!("{}", data.to_colored_json_auto().unwrap());
}
