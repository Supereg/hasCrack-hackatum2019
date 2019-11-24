import uuid from 'uuid/v4'; // Version 4, random uuid
import path from 'path';
import createDebug from 'debug';
import {spawn} from 'child_process'
import {OutputDataStorage} from "./storage";
import {once} from "./utils/once";

const debug = createDebug("hackatum2019-ui:ImageAnalyzer");

export enum AnalyzerErrorCodes {
    SUCCESS = 0,
    ERROR_STARTING = 1,
    ERROR_STOPPING = 2,
    NON_ZERO_EXIT = 3,
}

export type CompletionHandler = (error: AnalyzerErrorCodes) => void;

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

    private readonly inputFilename: string;
    private readonly outputFilename: string;

    //private readonly outputPath: string;
    //private readonly webOutputPath: string;

    constructor(id: string, filename: string) {
        this.id = id;
        this.storage = OutputDataStorage.initStore(id, filename); // create storage object

        this.inputFilename = this.storage.inputFilename;
        this.outputFilename = "output-" + id + ".png";
    }

    run(callback: CompletionHandler) {
        callback = once(callback); // ensure callback gets only called once

        const commands = "analyzer/hull.py ./public/images/" + this.inputFilename + " ./public/images/" + this.outputFilename;
        const script = spawn("python3", commands.split(" "), {env: process.env});

        let receivedData = false;
        let output = "";

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

            output += String(data);
        });
        script.stderr.on("data", data => {
            debug("Python process reports the following error: " + String(data));
        });

        script.on("exit", (code, signal) => {
            if (code !== 0) {
                debug("Python process exited with code %d", code);
                callback(AnalyzerErrorCodes.NON_ZERO_EXIT);
            } else {
                const outputData: Record<string, string> = {};
                const lines = output.split("\n");
                lines.forEach(line => {
                   const [key, value] = line.split(": ");
                   outputData[key] = value;
                });

                this.storage.update(this.outputFilename, outputData);
                this.storage.store();

                callback(AnalyzerErrorCodes.SUCCESS);
            }
        });
    }

}
