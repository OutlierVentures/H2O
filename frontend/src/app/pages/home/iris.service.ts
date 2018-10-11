import {Injectable} from '@angular/core';
import {Http} from "@angular/http";
import {Observable} from "rxjs/Observable";
import 'rxjs/add/operator/map';
import {
    Iris,
    ProbabilityPrediction,
    MLParams,
    MLResult
} from "./types";

const SERVER_URL: string = 'api/';

@Injectable()
export class MLService {

    constructor(private http: Http) {
    }

    public trainModel(MLParams: MLParams): Observable<MLResult> {
        return this.http.post(`${SERVER_URL}train`, MLParams).map((res) => res.json());
    }

    public predictIris(iris: Iris): Observable<ProbabilityPrediction[]> {
        return this.http.post(`${SERVER_URL}predict`, iris).map((res) => res.json());
    }
}
