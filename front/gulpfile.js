let gulp = require("gulp"),
  sass = require("gulp-sass"),
  spawn = require("child_process").spawn;

gulp.task("front", function (cb) {
  var cmd = spawn(/^win/.test(process.platform) ? "npm.cmd" : "npm", ["start"]); //https://github.com/nodejs/node-v0.x-archive/issues/5841
  cmd.stdout.on("data", data => {
    console.log(`stdout: ${data}`);
  });
  cmd.stderr.on("data", data => {
    console.log(`stderr: ${data}`);
  });
  cmd.on("close", function (code) {
    console.log("my-task exited with code " + code);
    cb(code);
  });
});

gulp.task("sass", function () {
  gulp
    .src(["./src/**/*.scss", "!./src/app/mixins/*.scss"], { base: "." })
    .pipe(sass().on("error", sass.logError))
    .pipe(gulp.dest("."));
});

gulp.task("watch-sass", function () {
  gulp.watch(["./src/**/*.scss"], ["sass"]);
});

gulp.task("default", ["front", "sass", "watch-sass"]);
