use wstd::http::{Body, Request, Response, StatusCode};

use image_recognition::inference_with_model;

mod image_recognition;

#[wstd::http_server]
async fn main(req: Request<Body>) -> Result<Response<Body>, wstd::http::Error> {
    match req.uri().path_and_query().unwrap().as_str() {
		"/" => Ok(Response::new("Hello from wasmCloud AI workload\n".into())),
        "/squeezenet" => {
			let mut body: Body = req.into_body();
			let bytes = body.contents().await?;
			let img = image::load_from_memory(bytes).unwrap();
            let result: String = inference_with_model(
                img,
                "fixture/models/squeezenet1.1-7.onnx",
            )
            .await.unwrap();
			Ok(Response::new(result.into()))
        }
        "/mobilenet" => {
			let mut body: Body = req.into_body();
			let bytes = body.contents().await?;
			let img = image::load_from_memory(bytes).unwrap();
            let result: String = inference_with_model(
                img,
                "fixture/models/mobilenetv2-7.onnx",
            )
            .await.unwrap();
			Ok(Response::new(result.into()))
        }
        _ => not_found(req).await,
    }
}

async fn not_found(_req: Request<Body>) -> Result<Response<Body>, wstd::http::Error> {
    Ok(Response::builder()
        .status(StatusCode::NOT_FOUND)
        .body("Not found\n".into())
        .unwrap())
}
