module.exports = function(config){
  var opalPath;
  var projectName = "lab";
  if(process.env.TRAVIS){
    python_version = process.env.TRAVIS_PYTHON_VERSION;
    opalPath = '/home/travis/virtualenv/python' + python_version + '/src/opal';
  }
  else{
    opalPath = '../../opal/opal';
  }
  var karmaDefaults = require(opalPath + '/tests/js_config/karma_defaults.js');
  var baseDir = '../' + __dirname;
  var coverageFiles = [
    __dirname + "/../" + projectName + "/static/js/" + projectName + "/**/*.js"
  ];
  var includedFiles = [
    __dirname + "/../" + projectName + "/static/js/" + projectName + "/**/*.js",
    __dirname + "/../" + projectName + "/static/js/" + projectName + "test/**/*.js",
  ];

  var defaultConfig = karmaDefaults(includedFiles, baseDir, coverageFiles);
  config.set(defaultConfig);
};
