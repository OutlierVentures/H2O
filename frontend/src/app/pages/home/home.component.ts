import {Component, OnInit} from '@angular/core';
import {MLService} from "./cluster.service";
import {
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
            window.location.reload();
        });
    }

    public trainModel() {
        this.mlService.trainModel(this.MLParams).subscribe((MLResult) => {
            this.MLResult = MLResult;
            window.location.reload();
        });
    }

}
