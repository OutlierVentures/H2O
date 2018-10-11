import {Component, OnInit} from '@angular/core';
import {MLService} from "./iris.service";
import {
    Iris,
    ProbabilityPrediction,
    MLParams,
    MLResult
} from "./types";

@Component({
    selector: 'home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

    public MLParams: MLParams = new MLParams();
    public MLResult: MLResult;
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
