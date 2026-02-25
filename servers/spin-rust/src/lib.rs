use std::{thread, time::Duration};

use spin_sdk::http::{IntoResponse, Request, Response};
use spin_sdk::http_component;

/// A simple Spin HTTP component.
#[http_component]
fn handle_spin_rust(req: Request) -> anyhow::Result<impl IntoResponse> {
    println!("Handling request to {:?}", req.header("spin-full-url"));
    match req.path_and_query().unwrap() {
        "/" => Ok(Response::builder()
            .status(200)
            .body("Hello from spin rust")
            .build()),
        "/wait" => {
            thread::sleep(Duration::from_secs(3));
            Ok(Response::builder()
                .status(200)
                .body("Waited for 3 seconds in spin rust")
                .build())
        }
        _ => Ok(Response::builder().status(404).body("Not found").build()),
    }
}
