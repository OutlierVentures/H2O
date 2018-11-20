export class MLParams {
    C: number = 4;
}

export class MLResult {
    accuracy: number;
}

export class OrbitParams {
    address: string = "/orbitdb/QmcHKBHmXmx3HHi1opqAVqF4E3qwwkmJPQ8CeVX4ybc4xJ/trainingdata"
    dataset: string;// = "{\"x\":[2.2532708777637005,0.12313498323398875,2.2434802870106925,2.6185854824861314,2.6492824176090286,3.2468399088648487,2.391414899939096,2.0211467187705625,0.569696937524268,1.6246546789055267,0.8204938124828087,2.1594050104713083,0.34987239852153196,2.118723567784688,1.742659685725724,2.528893505319752,1.6703094842102197,1.3408153596352634,0.16117090506347276,0.9246606526497161,1.682890110408658,1.8062512960867254,0.7826066698425189,0.3936951581548168,1.048291864126934,2.5156969333232873,2.5299779248957583,0.8023140038834188,1.7373444822434374,1.3973138161771175,0.7208675097620585,1.720396175444295,1.5988564087107986,1.4425497620177938,2.343562929740348,1.4815331952273267,2.1386042691191425,1.408488177976248,2.362307206605918,2.204386608535906,1.5914154189103553,2.996842869961005,1.7233096151252982,1.4513142873092897,0.5285367979496572,1.7079835915671953,1.468705818875798,1.8536790479462881,1.0649831496733715,1.5459704208181453,0.45199359601294875,1.5656598641263204,1.1774408991352696,1.8484580310530043,0.6591090317060133,1.420025022190011,2.060517531793288,3.0167385346730704,2.1111473905402987,1.009528689738079,2.233450720020079,2.4836828273842233,1.209101298411725,1.3567889411199918,0.9991493371972181,2.989047001646163,-0.3002248293705443,1.9100490736214788,1.1982016949192078,1.0537437913949532,1.8376907455720592,1.1328039293719456,0.1693211547675193,1.3096387250800752,0.7214439876706683,0.6400398546585195,0.5323772047314387,0.4408937677912238,0.522620896354874,0.9621789643771677,0.5408715039555542,2.006041259220162,1.71810119110419,1.9212658359571877,1.5551598477380955],\"y\":[0.35113290557268395,5.279175025064285,0.3479632646458396,0.3576979057562252,1.0561349659003616,1.3699034034331437,1.1013945780584922,1.7543350207626203,3.4406460262825513,1.8526961364874537,4.3318699985632625,1.385983178179793,4.692532505364345,1.0986583416602878,5.038466712398533,0.8201586133925197,1.1672882555838455,4.368278782827096,4.535178455211277,4.509086578417576,0.48444439060842964,1.8624296868464296,4.152635952160722,4.754200570925484,5.030924080929878,1.0570274864094475,0.9414392806305323,4.38196181200038,1.2358803074111866,0.6668713575305824,3.7134712353871837,5.251731915463681,1.4561718039858633,1.3198451481387103,0.7935142821489394,0.6787536375657198,1.21517937838399,3.932704817245169,1.3587669957212003,1.5608566082814521,4.904977251840595,0.22378412936671366,4.201208195565489,4.228108723299541,4.497238576378021,0.8228463897741014,1.8694742527625832,1.5088861951291506,4.102896859344259,3.686374417271564,3.5937783588589025,4.213824909542215,3.961382281978233,0.523936254217558,4.122416744454821,1.3823620140169424,1.7905989068908545,1.637921055655149,3.5766044901490077,4.455023276318281,1.2509502440339109,0.5721508632878634,3.535665484309778,4.364624835694804,4.210195402435473,1.3506859890756295,4.63059662516857,3.8151483875101846,4.470624491135523,4.492868587249477,1.8222955241776078,3.8767394577975276,4.197417187341405,1.1173595105702052,4.084750176642797,4.1240107466781195,3.3133890933364265,4.831013190913958,4.329760025346459,4.517953262713599,4.014362495066182,0.5659245167568832,0.9135789390751125,1.2988918578361344,0.12527811154913104],\"t\":[1,0,1,1,1,1,1,1,0,1,0,1,0,1,0,1,1,0,0,0,1,1,0,0,0,1,1,0,1,1,0,0,1,1,1,1,1,0,1,1,0,1,0,0,0,1,1,1,0,0,0,0,0,1,0,1,1,1,0,0,1,1,0,0,0,1,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,1,1,1,1]}"
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
    containername: string = "h2o-" + genid(); // Generates new Ocean asset ID when instantiated
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
