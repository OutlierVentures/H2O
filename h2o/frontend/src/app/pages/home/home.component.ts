import {Component, OnInit} from '@angular/core';
import {MLService} from "./cluster.service";
import {
    MLParams,
    MLResult,
    OrbitParams,
    OrbitResult,
    OceanParams,
    OceanResult
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
    public OceanParams: OceanParams = new OceanParams();
    public OceanResult: OceanResult;

    constructor(private mlService: MLService) {
    }

    ngOnInit() {
    }

    public getOrbit() {
        this.mlService.getOrbit(this.OrbitParams).subscribe((OrbitResult) => {
            this.OrbitResult = OrbitResult;
        });
        document.getElementById('replicate').innerHTML="<p><center>Finding nearest database...<center></p>";
    }

    public trainModel() {
        this.mlService.trainModel(this.MLParams).subscribe((MLResult) => {
            this.MLResult = MLResult;
        });
        location.reload();
    }

    public publishAsset() {
        // Not the prettiest, but fast and doesn't require any additional listening for backend outputs
        try {
            this.mlService.publishAsset(this.OceanParams).subscribe((OceanResult) => {
                this.OceanResult = OceanResult;
            });
            document.getElementById('form').innerHTML="<p>Successfully uploaded to Ocean Protocol!</p><img src=\"../../assets/images/success.png\" style=\"width: 30%\">";
            location.reload();
        }
        catch (e) {
            document.getElementById('form').innerHTML="</p>Could not connect to Ocean Protocol.</p><img src=\"../../assets/images/failure.png\" style=\"width: 30%\"><p><center>Check your account is the first in Keeper contracts<br />and ensure you set your environment variables.</center></p>";
        }
    }

}
