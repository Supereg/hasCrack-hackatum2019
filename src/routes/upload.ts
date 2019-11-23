import express, {Express, NextFunction, Request, Response, Router} from 'express';
import {Route} from "./Route";
import multer, {StorageEngine} from "multer";
import createDebug from 'debug';

const debug = createDebug("hackatum2019-ui:routes:upload");

export class UploadRoute implements Route {

    private readonly router: Router;
    private imageStore?: StorageEngine;

    constructor() {
        this.router = express.Router();
    }

    configure(app: Express) {
        this.imageStore = multer.diskStorage({
            destination: (request: Express.Request, file: Express.Multer.File, callback: (error: Error | null, destination:string) => void) => {
                if (file.mimetype !== 'image/jpeg') {
                    return callback(new Error("Invalid image format"), "");
                }
                callback(null, "./public/images/");
            },
            filename: (req: Express.Request, file: Express.Multer.File, callback: (error: (Error | null), filename: string) => void) => {
                callback(null, Date.now() + file.originalname);
            },
        });

        const upload = multer({
            storage: this.imageStore,
        });

        /* GET upload page */
        this.router.get('/', this.handleRoot.bind(this));
        this.router.post("/", upload.single("crack-image"), this.handleImageUploadNext.bind(this));
    }

    handleRoot(request: Request, response: Response, next: NextFunction) {
        response.render('upload', {});
    }

    handleImageUploadNext(request: Request, response: Response, next: NextFunction) {
        const fileData: Express.Multer.File = request.file;

        debug("Received image: %o", fileData);

        const imagePath = fileData.path.replace(/^public\//, "");
        debug("Redirecting to image location '%s'", imagePath);
        response.redirect(imagePath);
    }

    middleware(): Router {
        return this.router;
    }

}
