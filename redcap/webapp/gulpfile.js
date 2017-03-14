'use strict';

const gulp = require("gulp");
const sourcemaps = require("gulp-sourcemaps");
const babel = require("gulp-babel");
const minify = require('gulp-minify');
const cleanCSS = require('gulp-clean-css');

const sass = require('gulp-sass');

gulp.task("makejs", function () {
    return gulp.src("src/js/**/*.js")
        .pipe(sourcemaps.init())
        .pipe(babel({'presets':['es2015']}))
        .pipe(sourcemaps.write("."))
        .pipe(minify({
            ext:{
                src:'-debug.js',
                min:'.js'
            },
            exclude: ['tasks'],
            ignoreFiles: ['.combo.js', '-min.js']
        }))
        .pipe(gulp.dest("dist/js"));
});


gulp.task('makecss', function () {
    return gulp.src('src/scss/**/*.scss')
        .pipe(sourcemaps.init())
        .pipe(sass().on('error', sass.logError))
        .pipe(cleanCSS({compatibility: 'ie8'}))
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest('dist/css'));
});

gulp.task('sass:watch', function () {
    gulp.watch('src/scss/**/*.scss', ['makecss']);
});

gulp.task('makejs:watch', function () {
    gulp.watch('src/js/**/*.js', ['makejs']);
});