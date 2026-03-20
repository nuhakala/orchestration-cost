use spin_sdk::http::{IntoResponse, Request, Response};
use spin_sdk::http_component;

use image_recognition::inference_with_model;

mod image_recognition;

/// A simple Spin HTTP component.
#[http_component]
async fn handle_spin_ai(req: Request) -> anyhow::Result<impl IntoResponse> {
    match req.path_and_query().unwrap() {
        "/" => Ok(Response::builder()
            .status(200)
            .header("content-type", "text/plain")
            .body("Hello from Spin AI workload")
            .build()),
        "/mobilenet" => {
            let img = image::load_from_memory(req.body()).unwrap();
            let result: String = inference_with_model(img, "fixture/models/mobilenetv2-7.onnx")
                .await
                .unwrap();
            Ok(Response::builder()
                .status(200)
                .header("content-type", "text/plain")
                .body(result.as_str())
                .build())
        }
        "/squeezenet" => {
            let img = image::load_from_memory(req.body()).unwrap();
            let result: String = inference_with_model(img, "fixture/models/squeezenet1.1-7.onnx")
                .await
                .unwrap();
            Ok(Response::builder()
                .status(200)
                .header("content-type", "text/plain")
                .body(result.as_str())
                .build())
        }
        _ => Ok(Response::builder().status(404).body("Not found").build()),
    }
}
