import createError from 'http-errors';
import express, {Request} from 'express';
import path from 'path';
import cookieParser from 'cookie-parser';
import logger from 'morgan';
import {UploadRoute} from "./routes/upload";
import {ViewRoute} from "./routes/view";
import {NextFunction, Response} from "express-serve-static-core";

const app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

const uploadRoute = new UploadRoute();
const viewRoute = new ViewRoute();
uploadRoute.configure(app);
viewRoute.configure(app);

app.get("/", (request: Request, response: Response, next: NextFunction) => {
  response.redirect("/upload");
});
app.use('/upload', uploadRoute.middleware());
app.use('/view', viewRoute.middleware());

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err: any, req: any, res: any, next: any) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
