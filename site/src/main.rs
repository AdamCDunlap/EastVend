extern crate iron;
extern crate router;
extern crate urlencoded;

use iron::prelude::*;
use iron::{AfterMiddleware};
use iron::status;

use urlencoded::UrlEncodedBody;

use std::path::{Path,PathBuf};
use std::io;
use std::io::Write;
use std::fs::File;

struct Custom404 {
    path_buf: PathBuf
}

impl Custom404 {
    fn new(filename: &str) -> Custom404 {
        Custom404 { path_buf: PathBuf::from(filename) }
    }
}

impl AfterMiddleware for Custom404 {
    fn catch(&self, _: &mut Request, err: IronError) -> IronResult<Response> {
        if err.response.status == Some(status::NotFound) {
            Ok(Response::with((status::Ok, self.path_buf.as_path())))
        } else {
            Err(err)
        }
    }
}

struct ValidUser {
    name: String,
    student_id: u32,
    email: String,
    notify_freq_days: u8,
}

impl ValidUser {
    fn from_request(req: &mut Request) -> Option<ValidUser> {
        req.get_ref::<UrlEncodedBody>().ok().and_then(|ref hash| {
            let name = match hash.get("name").and_then(|v| v.first()) {
                Some(ref name) => (*name).clone(),
                _ => return None
            };
            let student_id = match hash.get("student_id").and_then(|v| v.first()) {
                Some(ref student_id) => match student_id.parse::<u32>() {
                    Ok(id) => {
                        if (id >= 10000000) && (id < 100000000) {
                            id
                        } else { return None }
                    }
                    _ => return None
                },
                _ => return None
            };
            let email = match hash.get("email").and_then(|v| v.first()) {
                Some(ref email) => (*email).clone(),
                _ => return None
            };
            let notify_frequency = match hash.get("notify_frequency").and_then(|v| v.first()) {
                Some(ref notify_frequency) => match notify_frequency.as_ref() {
                    "immediately" => 0,
                    "daily" => 1,
                    "weekly" => 7,
                    _ => return None
                },
                _ => return None
            };
            Some(ValidUser{
                name: name, student_id: student_id,
                email: email, notify_freq_days: notify_frequency
            })
        })
    }
    fn write_to_file(&self, dir: &str) -> io::Result<()> {
        let mut file = try!(File::create(format!("{}/{}", dir, self.student_id)));
        file.write_fmt(format_args!("0\x000\x00{}\x00{}\x00{}", self.email, self.notify_freq_days, self.name))
    }
}

fn user_registration(req: &mut Request) -> IronResult<Response> {
    // TODO: Verify request is a POST (see req.method)
    ValidUser::from_request(req).and_then(|valid_user| {
        valid_user.write_to_file("./").ok()
    }).map(|_| serve_index(req)).unwrap_or(
        Ok(Response::with((status::BadRequest, "Malformed POST submission")))
    )
}

fn serve_index(_: &mut Request) -> IronResult<Response> {
    Ok(Response::with((status::Ok, Path::new("static/index.html"))))
}

fn main() {
    let mut router = router::Router::new();
    router.get("/", serve_index);
    router.post("/confirm", user_registration);

    let mut chain = Chain::new(router);
    let my_404 = Custom404::new("static/404.html");
    chain.link_after(my_404);

    Iron::new(chain).http("localhost:3000").unwrap();
}
