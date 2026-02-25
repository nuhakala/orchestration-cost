use std::{thread, time::Duration};

use rocket::response::status;

#[macro_use] extern crate rocket;
const SLEEP: u64 = 3;

#[get("/")]
fn index() -> &'static str {
    "Hello from Rust!\n"
}

#[get("/wait")]
fn wait() -> status::Accepted<String> {
	thread::sleep(Duration::from_secs(SLEEP));
	status::Accepted(format!("Slept for {SLEEP} seconds in Rust!\n"))
}

#[launch]
fn rocket() -> _ {
	// Print the figment, we can read the active config from there
	println!("{:#?}", rocket::Config::figment());

	// Configuration in Rocket.toml
	rocket::build()
		.mount("/", routes![index])
		.mount("/", routes![wait])
}
