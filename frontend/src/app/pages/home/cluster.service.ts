import {Injectable} from '@angular/core';
import {Http} from "@angular/http";
import {Observable} from "rxjs/Observable";
import 'rxjs/add/operator/map';
import {
    MLParams,
    MLResult,
    OrbitParams,
    OrbitResult,
    OceanParams,
    OceanResult
} from "./types";

const SERVER_URL: string = 'api/';

@Injectable()
export class MLService {

    constructor(private http: Http) {
    }

    public getOrbit(OrbitParams: OrbitParams): Observable<OrbitResult> {
        return this.http.post(`${SERVER_URL}orbit`, OrbitParams).map((res) => res.json());
    }

    public trainModel(MLParams: MLParams): Observable<MLResult> {
        return this.http.post(`${SERVER_URL}train`, MLParams).map((res) => res.json());
    }

    public publishAsset(OceanParams: OceanParams): Observable<OceanResult> {
        return this.http.post(`${SERVER_URL}ocean`, OceanParams).map((res) => res.json());
    }

}
