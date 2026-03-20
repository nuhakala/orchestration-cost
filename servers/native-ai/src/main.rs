use rocket::response::status;
use rocket::data::ToByteUnit;

use image_recognition::inference_with_model;

mod image_recognition;

#[macro_use]
extern crate rocket;

#[get("/")]
fn index() -> &'static str {
    "Hello from AI Rust!\n"
}

#[post("/squeezenet", data = "<body>")]
async fn squeezenet(body: rocket::Data<'_>) -> status::Accepted<String> {
    let bytes = body.open(10.mebibytes()).into_bytes().await.unwrap();
    let img = image::load_from_memory(&bytes).unwrap();
    let result: String = inference_with_model(img, "/fixture/models/squeezenet1.1-7.onnx")
        .await
        .unwrap();
    status::Accepted(result)
}

#[post("/mobilenet", data = "<body>")]
async fn mobilenet(body: rocket::Data<'_>) -> status::Accepted<String> {
    let bytes = body.open(10.mebibytes()).into_bytes().await.unwrap();
    let img = image::load_from_memory(&bytes).unwrap();
    let result: String = inference_with_model(img, "/fixture/models/mobilenetv2-7.onnx")
        .await
        .unwrap();
    status::Accepted(result)
}

#[launch]
fn rocket() -> _ {
    // Print the figment, we can read the active config from there
    println!("{:#?}", rocket::Config::figment());

    // Configuration in Rocket.toml
    rocket::build()
        .mount("/", routes![index])
        .mount("/", routes![mobilenet])
        .mount("/", routes![squeezenet])
}
