import createDebug from 'debug';
import fs from 'fs';
import assert from 'assert';
import {json} from "express";

const debug = createDebug("hackatum2019-ui:DataStorage");

type FileStructure = {
    version: number,
    inputFilename: string,
    outputFilename: string,
    results: string,
}

export class OutputDataStorage {

    private static readonly currentVersion = 1;

    private static readonly PATH = "./output/";
    private static readonly FILE_EXT = ".json";

    static initStore(id: string, filename: string) {
        const content: Partial<FileStructure> = {
            inputFilename: filename,
        };

        debug("Initializing new store for %s", id);

        const storage = new OutputDataStorage(id, content);
        storage.store();

        return storage;
    }

    static load(id: string, callback: (err: NodeJS.ErrnoException | null, data?: OutputDataStorage) => void) {
        debug("Loading id %s...", id);
        fs.readFile(this.PATH + id + this.FILE_EXT, {
            encoding: 'utf8',
        }, (err, data) => {
            if (err) {
                debug("Failed to load data for given id");
                callback(err);
            } else {
                debug("Successfully found data for given id");
                const jsonContent: Partial<FileStructure> = JSON.parse(data);
                assert(jsonContent.version === this.currentVersion, "Encountered unknown file version");
                assert(jsonContent.inputFilename !== undefined, "Input file is undefined!");

                const storage = new OutputDataStorage(id, jsonContent);
                callback(null, storage);
            }
        });
    }

    readonly id: string;

    readonly inputFilename: string;
    outputFilename?: string;
    results?: string;

    private constructor(id: string, content: Partial<FileStructure>) {
        this.id = id;

        this.inputFilename = content.inputFilename!;
        this.outputFilename = content.outputFilename;
        this.results = content.results;
    }

    update(outputFilename: string, results: string) {
        this.outputFilename = outputFilename;
        this.results = results;
    }

    store() {
        const content: Partial<FileStructure> = {
            version: OutputDataStorage.currentVersion,
            inputFilename: this.inputFilename,
            outputFilename: this.outputFilename,
            results: this.results,
        };

        const jsonContent = JSON.stringify(content);
        fs.writeFile(OutputDataStorage.PATH + this.id + OutputDataStorage.FILE_EXT, jsonContent, 'utf8', error => {
            if (error) {
                debug("Failed to create storage");
                return; // TODO display error
            }

            debug("Create new json storage!");
        });
    }

}
