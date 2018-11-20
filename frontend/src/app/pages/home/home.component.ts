import 'setimmediate'

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
        
        document.getElementById('replicate').innerHTML="<p><center>Finding nearest database...<center></p>";
        
        console.log('before')

        this.getODB(() => {
            console.log('OrbitDB retrieved');    

            this.mlService.getOrbit(this.OrbitParams).subscribe((OrbitResult) => {
                this.OrbitResult = OrbitResult;
            });
            location.reload();
        });
        //document.getElementById('replicate').innerHTML="<p><center>Finding nearest database...<center></p>";
        //setTimeout(() => location.reload(), 10000);
    }

    public trainModel() {
        this.mlService.trainModel(this.MLParams).subscribe((MLResult) => {
            this.MLResult = MLResult;
        });
        location.reload();
    }

    public publishAsset() {
        try {
            this.mlService.publishAsset(this.OceanParams).subscribe((OceanResult) => {
                this.OceanResult = OceanResult;
            });
            document.getElementById('form').innerHTML="\
            <p>Successfully uploaded to Ocean Protocol!</p>\
            <img src=\"../../assets/images/success.png\" style=\"width: 30%\">\
            <p><center><a href=\"https://" + this.OceanParams.azureaccount + 
            ".blob.core.windows.net/" + this.OceanParams.containername +
            "/output.json\">Your hosted dataset</a><br/>\
            (Will 404 if account invalid)</center></p>";
        }
        catch (e) {
            document.getElementById('form').innerHTML="\
            </p>Could not connect to Ocean Protocol.</p>\
            <img src=\"../../assets/images/failure.png\" style=\"width: 30%\">\
            <p><center>Check your account is the first in Keeper contracts<br />\
            and ensure you set your environment variables.</center></p>";
            setTimeout(() => location.reload(), 10000);
        }
    }

    private getODB(_callback) {

        const IPFS = require('ipfs')
        const OrbitDB = require('orbit-db')

        const ipfsOptions = {
            start: true,
            EXPERIMENTAL: {
                pubsub: true,
            },
            config: {
                Addresses: {
                    Swarm: [
                        '/dns4/ws-star.discovery.libp2p.io/tcp/443/wss/p2p-websocket-star',
                    ]
                },
            }
        }

        const ipfs = new IPFS(ipfsOptions)

        ipfs.on('error', (e) => console.error(e))

        ipfs.on('ready', async () => {

            const orbitdb = new OrbitDB(ipfs)

            const db = await orbitdb.open(this.OrbitParams.address)
            await db.load()

            db.events.on('replicated', async () => {
                try {
                    let data = {
                        "x": this.getArray(db, 'x'),
                        "y": this.getArray(db, 'y'),
                        "t": this.getArray(db, 't')
                    }
                    this.OrbitParams.dataset = JSON.stringify(data);
                    console.log('Has been set!')
                    console.log(this.OrbitParams.dataset)
                    //_callback();
                    await orbitdb.disconnect()
                    await ipfs.stop(() => {})
                    _callback();
                }
                catch(error) {
                    // OrbitDB considers itself loaded before it is readable, catch this
                    console.log(error)
                    _callback()
                }

            })

        })
        
    }
    private getArray(db, name) {

        let entry = db.get(name)
        return entry[0].array

    }




}
