import {Component, OnInit} from '@angular/core';
import {MLService} from "./iris.service";
import {
    Iris,
    ProbabilityPrediction,
    MLParams,
    MLResult,
    OrbitParams,
    OrbitResult
} from "./types";

@Component({
    selector: 'home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

    public MLParams: MLParams = new MLParams();
    public MLResult: MLResult;
    public OrbitParams: OrbitParams = new OrbitParams();
    public OrbitResult: OrbitResult;
    public iris: Iris = new Iris();
    public probabilityPredictions: ProbabilityPrediction[];

    // graph styling
    public colorScheme = {
        domain: ['#1a242c', '#e81746', '#e67303', '#f0f0f0']
    };

    constructor(private mlService: MLService) {
    }

    ngOnInit() {
    }

    public getOrbit() {
        this.mlService.getOrbit(this.OrbitParams).subscribe((OrbitResult) => {
            this.OrbitResult = OrbitResult;
        });
    }

    public trainModel() {
        this.mlService.trainModel(this.MLParams).subscribe((MLResult) => {
            this.MLResult = MLResult;
        });
    }

    public predictIris() {
        this.mlService.predictIris(this.iris).subscribe((probabilityPredictions) => {
            this.probabilityPredictions = probabilityPredictions;
        });
    }

}
