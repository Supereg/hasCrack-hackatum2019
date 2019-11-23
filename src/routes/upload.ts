import express, {Express, NextFunction, Request, Response, Router} from 'express';
import {Route} from "./Route";
import multer, {Instance, StorageEngine} from "multer";
import createDebug from 'debug';
import {AnalyzerErrorCodes, ImageAnalyzer} from "../image-analyzer";
import {OutputDataStorage} from "../storage";

const debug = createDebug("hackatum2019-ui:routes:upload");

export class UploadRoute implements Route {

    private readonly router: Router;

    private readonly imageStore: StorageEngine;
    private readonly multer: Instance;

    constructor() {
        this.router = express.Router();

        this.imageStore = multer.diskStorage({
            destination: this.handleImageDestination.bind(this),
            filename: this.handleUploadFilename.bind(this),
        });
        this.multer = multer({
            storage: this.imageStore,
        });
    }

    configure(app: Express) {
        /* GET upload page */
        this.router.get('/', this.handleRoot.bind(this));
        this.router.post("/", this.multer.single("crack-image"), this.handleImageUploadCompleted.bind(this));
    }

    handleRoot(request: Request, response: Response, next: NextFunction) {
        response.render('upload', {
            title: "Upload a file",
        });
    }

    private handleImageUploadCompleted(request: Request, response: Response, next: NextFunction) {
        const fileData: Express.Multer.File = request.file;

        if (!fileData) { // the user didn't select a file
            response.render("upload-error", { // TODO unite that with upload page
                error: "Please upload a file",
            });
            return;
        }

        debug("Received image: %o", fileData);

        const id = ImageAnalyzer.idFrom(fileData.filename);

        const imageAnalyzer = new ImageAnalyzer(id, fileData.filename);
        imageAnalyzer.run((error, result) => {
            if (error) {
                debug("Returned with error %s", AnalyzerErrorCodes[error]);
                response.render("upload-error", { // TODO unite that with upload page
                    error: AnalyzerErrorCodes[error], // TODO friendly names
                })
            } else {
                debug("Returned with data: %o", result);

                const viewPage = "view?id=" + id;
                debug("Redirecting to image location '%s'", viewPage);
                response.redirect(viewPage);
            }
        });
    }

    private handleImageDestination(request: Express.Request, file: Express.Multer.File, callback: (error: Error | null, destination:string) => void) {
        if (file.mimetype !== 'image/jpeg') {
            return callback(new Error("Invalid image format"), "");
        }
        callback(null, "./public/images/");
    }

    private handleUploadFilename(req: Express.Request, file: Express.Multer.File, callback: (error: (Error | null), filename: string) => void) {
        const filename = ImageAnalyzer.generateNewIdFrom(file.originalname);
        callback(null, filename);
    }

    middleware(): Router {
        return this.router;
    }

}
