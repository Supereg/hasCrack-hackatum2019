import express, {Express, NextFunction, Request, Response} from 'express';
import createDebug from 'debug';
import {Route} from "./Route";
import {Router} from "express";
import {AnalyzerErrorCodes, ImageAnalyzer} from "../image-analyzer";
import {OutputDataStorage} from "../storage";

const debug = createDebug("hackatum2019-ui:routes:view");

export class ViewRoute implements Route {

    private static readonly VIEW = "view";

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
            response.render(ViewRoute.VIEW, {
                error: "Please supply a result id"
            });
            return;
        }

        OutputDataStorage.load(id, (error, data) => {
           if (error) {
               response.render(ViewRoute.VIEW, {
                   error: "Could not open output for given id. Are you sure this id exists?",
               });
           } else {
               const rating = data!.results["rating"];
               const lossArea = data!.results["loss-area"];

               let ratingPercentage = rating? parseFloat(rating): -1;
               let lossAreaPercentage = lossArea? parseFloat(lossArea): -1;

               if (ratingPercentage >= 0) {
                   ratingPercentage = Math.round(ratingPercentage * 100) / 100;
               }
               if (lossAreaPercentage >= 0) {
                   lossAreaPercentage = Math.round(lossAreaPercentage * 100) / 100;
               }

               response.render(ViewRoute.VIEW, {
                   //title: id,
                   source: "images/" + data!.inputFilename,
                   output: "images/" + data!.outputFilename,
                   crackSeverity: ratingPercentage + "%",
                   lostArea: lossAreaPercentage + "%",
               });
           }
        });
    }

    middleware(): Router {
        return this.router;
    }

}
