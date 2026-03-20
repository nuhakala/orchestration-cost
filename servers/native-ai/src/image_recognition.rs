use std::error::Error;
use std::fs;
use image::DynamicImage;
use tract_onnx::prelude::*;

pub async fn inference_with_model(
	img: DynamicImage,
    model: &str,
) -> Option<String> {
    let model = tract_onnx::onnx()
        .model_for_path(model)
		.expect("Should create a model from file")
        .into_optimized()
		.expect("Should optimize model")
        .into_runnable()
		.expect("Should turn model into runnable");

    let tensor = tensor_from_image(img);
    let result = model.run(tvec!(tensor.into())).expect("Should get results");

    let mut body = get_scores(result).unwrap();
    body = format!("Using model MobileNet\n{}", body);
	return Some(body);
}

fn get_scores(result: smallvec::SmallVec<[TValue; 4]>) -> Option<String> {
    let scores: Vec<f64> = result[0]
        .to_array_view::<f32>()
        .ok()?
        .iter()
        .map(|&x| x as f64)
        .collect();
    let array_f64: Vec<f64> = scores.iter().map(|&x| x as f64).collect();
    let array_slice: &[f64] = &array_f64;
    let mut percentages: Vec<(f64, u32)> = compute::functions::softmax(array_slice)
        .iter()
        .cloned()
        .zip(1..)
        .collect();
    percentages.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
    percentages.reverse();
    let top5 = &percentages[..5];
    let mut body = String::from("Top 5 predictions:\n");
    for (score, index) in top5 {
        let percentage = score * 100.0;
        let category = get_category("/fixture/labels/squeezenet1.1-7.txt", *index as usize).unwrap();
        body.push_str(&format!("Class {}: {:.1}\n", category, percentage));
    }
    return Some(body);
}

fn get_category(filename: &str, index: usize) -> Result<String, Box<dyn Error>> {
    // Read the whole file as a string
    let contents = fs::read_to_string(filename)?;

    // Split into lines
    let lines: Vec<&str> = contents.lines().collect();
    let index = index - 1; // Line indexing starts from 0

    // Make sure index is within bounds
    if index < lines.len() {
        let line = lines[index].to_string();
        let category_name = line
            .split_whitespace()
            .skip(1)
            .collect::<Vec<&str>>()
            .join(" ");
        Ok(category_name)
    } else {
        Err(format!("Index {} out of range", index).into())
    }
}

fn tensor_from_image(image: DynamicImage) -> Tensor {
    // open image, resize it and make a Tensor out of it
    // let image = image::open(img).unwrap().to_rgb8();
    let resized =
        image::imageops::resize(&image, 224, 224, ::image::imageops::FilterType::Triangle);
    let image: Tensor = tract_ndarray::Array4::from_shape_fn((1, 3, 224, 224), |(_, c, y, x)| {
        let mean = [0.485, 0.456, 0.406][c];
        let std = [0.229, 0.224, 0.225][c];
        (resized[(x as _, y as _)][c] as f32 / 255.0 - mean) / std
    })
    .into();
    return image;
}
