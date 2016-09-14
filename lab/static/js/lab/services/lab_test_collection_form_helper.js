angular.module('opal.services').factory('LabTestCollectionFormHelper', function(){
  "use strict";
  var DATE_FORMAT = 'DD/MM/YYYY';

  var LabTestCollectionFormHelper = function(labTestCollection){
      if(!labTestCollection.lab_tests){
        labTestCollection.lab_tests = [];
      }

      _.each(labTestCollection.lab_tests, function(lt){
        if(!lt.date_ordered){
          lt.date_ordered = new Date();
        }

        if(!lt.status){
          lt.status = 'pending';
        }
      });

      this.preSave = function(editing){
        _.each(editing.lab_test_collection.lab_tests, function(lt){
          _.each(["date_ordered", "date_received"], function(dt){
            if(lt[dt]){
                lt[dt] = moment(lt[dt]).format(DATE_FORMAT);
            }
          });
        });
      };
  };

  return LabTestCollectionFormHelper;
});
