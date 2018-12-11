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
        setTimeout(() => location.reload(), 10000);
    }

    public trainModel() {
        this.mlService.trainModel(this.MLParams).subscribe((MLResult) => {
            this.MLResult = MLResult;
        });
        location.reload();
    }

    public publishAsset() {
        try {
            let params = this.OceanParams;
            this.mlService.publishAsset(params).subscribe((OceanResult) => {
                this.OceanResult = OceanResult;
            });
            let startbutton = "<button _ngcontent-c8 class=\"mat-raised-button\" md-raised-button>\
                               <span class=\"mat-button-wrapper\">"
            let endbutton = "</span></button>"
            let azure = "";
            let etherscan = "";
            if (params.azureaccount != null && params.azurekey != null) {
                azure = "<a href=\"https://" + params.azureaccount + ".blob.core.windows.net/" + params.containername + "/output.json\">"
                        + startbutton + "Your hosted dataset" + endbutton
                        + "</a>";
            }
            if (params.publisher != null) {
                etherscan = "<a href=\"https://kovan.etherscan.io/address/" + params.publisher + "\">"
                            + startbutton + "Your contracts on Kovan" + endbutton
                            + "</a>";
            }
            document.getElementById('form').innerHTML="\
            <p>Successfully uploaded to Ocean Protocol!<br/><br/></p>\
            <img src=\"../../assets/images/success.png\" style=\"width: 30%\">\
            <p><center>"
            + azure
            + "<br/><br/>"
            + etherscan
            + "</center></p>";
        }
        catch (e) {
            document.getElementById('form').innerHTML="\
            </p>Could not connect to Ocean Protocol.<br/><br/></p>\
            <img src=\"../../assets/images/failure.png\" style=\"width: 30%\">\
            <p><center>Check your account is the first in Keeper contracts<br />\
            and ensure you set your environment variables.</center></p>";
            setTimeout(() => location.reload(), 10000);
        }
    }

}
