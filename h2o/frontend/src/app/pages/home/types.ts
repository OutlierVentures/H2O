export class MLParams {
    C: number = 4;
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
    assetid: string = genid(); // Generates new Ocean asset ID when instantiated
}

export class OceanResult {

}

// The goal is not randomness but collision resistance
function genid() {
    var text = "";
    var charspace = "abcdefghijklmnopqrstuvwxyz";
    for (var len = 0; len < 40; len++) {
      text += charspace.charAt(Math.floor(Math.random() * charspace.length));
    }
    return text;
  }
