module.exports = function(config){
  var opalPath;
  var projectName = "lab";
  if(process.env.TRAVIS){
    python_version = process.env.TRAVIS_PYTHON_VERSION;
    opalPath = '/home/travis/virtualenv/python' + python_version + '/src/opal';
  }
  else{
    opalPath = '../../opal';
  }
  var karmaDefaults = require(opalPath + '/config/karma_defaults.js');
  var karmaDir = __dirname;
  var coverageFiles = [
    __dirname + "/../" + projectName + "/static/js/" + projectName + "/**/*.js"
  ];
  var includedFiles = [
    __dirname + "/../" + projectName + "/static/js/" + projectName + "/**/*.js",
    __dirname + "/../" + projectName + "/static/js/" + projectName + "test/**/*.js",
  ];

  var defaultConfig = karmaDefaults(karmaDir, coverageFiles, includedFiles);
  config.set(defaultConfig);
};
