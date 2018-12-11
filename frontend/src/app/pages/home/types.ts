export class MLParams {
    clusters: number = 4;
}

export class MLResult {
    accuracy: number;
}

export class OrbitParams {
    address: string = "/orbitdb/QmcHKBHmXmx3HHi1opqAVqF4E3qwwkmJPQ8CeVX4ybc4xJ/trainingdata"
}

export class OrbitResult {

}

export class OceanParams {
    name: string = "H2O clustering";
    description: string = "Clustered OrbitDB";
    price: number = 10;
    author: string = "Outlier Ventures";
    azureaccount: string;
    azurekey: string;
    // Generates new Ocean asset ID when instantiated
    containername: string = "h2o-" + genid();
    // Overwritten if running with Kovan testnet
    publisher: string;
}

export class OceanResult {

}

// Unique container name - requires non-collision * under a single Azure account *
// 36^4=1679616 possibilities, Pr[collision] = 1 - ( (36^4-1)/36^4 )^num_datasets_created
function genid() {
    var text = "";
    var charspace = "abcdefghijklmnopqrstuvwxyz0123456789";
    for (var len = 0; len < 4; len++) {
      text += charspace.charAt(Math.floor(Math.random() * charspace.length));
    }
    return text;
}
