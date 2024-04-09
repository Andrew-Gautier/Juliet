use pyo3::prelude::*;
use regex::Regex;

#[pyfunction]
fn keep_newlines_spaces(input: &str) -> String {
    let initial_linecount = input.lines().count();
    let modified = Regex::new(r#"//.*|(?s)/\*.*?\*/"#).unwrap()
              .replace_all(input, |caps: &regex::Captures| caps[0].chars().map(|c| if c == '\n' || c == '\r' { c } else { ' ' }).collect::<String>())
              .to_string();
    assert_eq!(initial_linecount, modified.lines().count());
    modified
}

#[pyfunction]
fn keep_newlines(input: &str) -> String {
    let initial_linecount = input.lines().count();
    let modified = Regex::new(r#"// .*|(?s)/\*.*?\*/"#).unwrap()
              .replace_all(input, |caps: &regex::Captures| caps[0].chars().filter(|&c| c == '\n' || c == '\r').collect::<String>())
              .to_string();
    assert_eq!(initial_linecount, modified.lines().count());
    modified
}

#[pyfunction]
fn keep_nothing(input: &str) -> String {
    let modified = Regex::new(r#"// .*|(?s)/\*.*?\*/"#).unwrap()
              .replace_all(input, "")
              .to_string();
    modified
}

#[pymodule]
fn rcmpy(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(keep_newlines_spaces, m)?)?;
    m.add_function(wrap_pyfunction!(keep_newlines, m)?)?;
    m.add_function(wrap_pyfunction!(keep_nothing, m)?)?;
    Ok(())
}
