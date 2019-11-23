import uuid from 'uuid/v4'; // Version 4, random uuid
import path from 'path';
import createDebug from 'debug';
import {spawn} from 'child_process'
import {OutputDataStorage} from "./storage";
import {once} from "./utils/once";

const debug = createDebug("hackatum2019-ui:ImageAnalyzer");

export type AnalyzerResult = {
    inputFilename: string,
    outputFilename: string,
    outputText: string,
}

export enum AnalyzerErrorCodes {
    SUCCESS = 0,
    ERROR_STARTING = 1,
    ERROR_STOPPING = 2,
    NON_ZERO_EXIT = 3,

}

export type CompletionHandler = (error: AnalyzerErrorCodes, result?: AnalyzerResult) => void;

export class ImageAnalyzer {

    static generateNewIdFrom(filename: string): string {
        const fileExtension = path.extname(filename);

        return uuid() + fileExtension;
    }

    static idFrom(filename: string): string {
        return path.parse(filename).name;
    }

    private readonly id: string;
    private readonly storage: OutputDataStorage;

    private readonly imagePath: string;
    private readonly webImagePath: string;

    constructor(id: string, filename: string) {
        this.id = id;
        this.storage = OutputDataStorage.initStore(id, filename); // create storage object

        this.webImagePath = "images/" + this.storage.inputFilename;
        this.imagePath = "./public/" + this.webImagePath;
    }

    run(callback: CompletionHandler) {
        callback = once(callback); // ensure callback gets only called once

        const commands = "exec.py -file " + this.imagePath + "";
        const script = spawn("python", commands.split(" "), {env: process.env});

        let receivedData = false;
        const bufferList: Buffer[] = [];

        script.on("error", error => {
            if (!receivedData) {
                debug("Failed to spawn python process: " + error.message);
                callback(AnalyzerErrorCodes.ERROR_STARTING);
            } else {
                debug("Failed to kill python process: " + error.message);
                callback(AnalyzerErrorCodes.ERROR_STOPPING);
            }
        });
        script.stdout.on("data", (data: Buffer) => {
            if (!receivedData) { // received data after it was closed
                receivedData = true;
            }

            bufferList.push(data);
        });
        script.stderr.on("data", data => {
            debug("Python process reports the following error: " + String(data));
        });

        script.on("exit", (code, signal) => {
            if (code !== 0) {
                debug("Python process exited with code %d", code);
                callback(AnalyzerErrorCodes.NON_ZERO_EXIT);
            } else {
                const buf = Buffer.concat(bufferList);

                const outputFilename = "images/TODO.jpg";
                const outputText = buf.toString();

                const analyzerResult: AnalyzerResult = {
                    inputFilename: this.webImagePath,
                    outputFilename: outputFilename,
                    outputText: outputText,
                };

                this.storage.update(outputFilename, outputText);
                this.storage.store();

                callback(AnalyzerErrorCodes.SUCCESS, analyzerResult);
            }
        });
    }

}
