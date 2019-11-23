import express, {Express, Router} from "express";

export interface Route {

    configure(app: Express): void;

    middleware(): Router;

}
