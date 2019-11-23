import express, {Express, NextFunction, Request, Response} from 'express';
import createDebug from 'debug';
import {Route} from "./Route";
import {Router} from "express";
import {AnalyzerErrorCodes, ImageAnalyzer} from "../image-analyzer";
import {OutputDataStorage} from "../storage";

const debug = createDebug("hackatum2019-ui:routes:view");

export class ViewRoute implements Route {

    private readonly router: Router;

    constructor() {
        this.router = express.Router();
    }

    configure(app: Express): void {
        /* GET home page. */
        this.router.get('/', this.handleRoot.bind(this));

    }

    handleRoot(request: Request, response: Response, next: NextFunction) {
        const id = request.query.id;
        if (!id) {
            return next(new Error("Please supply id")); // TODO error page
        }

        OutputDataStorage.load(id, (error, data) => {
           if (error) {
               response.render('view', {
                   title: "Error: " + error.message, // TODO do not print that
               });
           } else {
               response.render('view', {
                   title: id,
               });
           }
        });
    }

    middleware(): Router {
        return this.router;
    }

}
