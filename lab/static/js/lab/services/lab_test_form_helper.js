angular.module('opal.services').factory('LabTestFormHelper', function(Metadata){
  "use strict";
  var DATE_FORMAT = 'DD/MM/YYYY';
  var DATETIME_FORMAT = 'DD/MM/YYYY HH:mm:ss';

  // TODO this functions should be part of the
  // field translator


  var castTo = function(someFormat, someValue){
    if(_.isDate(someValue)){
      return someValue;
    }
    if(moment.isMoment(someValue)){
      return moment.toDate();
    }
    if(someValue){
      return moment(someValue, someFormat).toDate();
    }
  };

  var castFrom = function(someFormat, someValue){
    if(someValue){
      return moment(someValue).format(someFormat);
    }
  };

  var castToDate = _.partial(castTo, DATE_FORMAT);
  var castToDateTime = _.partial(castTo, DATETIME_FORMAT);
  var castFromDate = _.partial(castFrom, DATE_FORMAT);
  var castFromDateTime = _.partial(castFrom, DATETIME_FORMAT);

  var dateFields = ["date_ordered", "date_received"];
  var datetimeFields = ["created", "updated"];

  var LabTestFormHelper = function(labTest){
      var self = this;
      if(!labTest.observations){
        labTest.observations = [];
      }

      _.each(labTest.observations, function(lt){
        if(!lt.date_ordered){
          lt.date_ordered = new Date();
        }
        else{
          lt.date_ordered = castToDate(lt.date_ordered);
        }

        lt.date_received = castToDate(lt.date_received);

        _.each(datetimeFields, function(dtField){
          lt[dtField] = castToDateTime(lt[dtField]);
        });

        if(!lt.status){
          lt.status = 'pending';
        }
      });

      this.preSave = function(editing){
        _.each(editing.lab_test.observations, function(lt){
          _.each(dateFields, function(dt){
            if(lt[dt]){
                lt[dt] = castFromDate(lt[dt]);
            }
          });

          _.each(datetimeFields, function(dt){
            if(lt[dt]){
                lt[dt] = castFromDateTime(lt[dt]);
            }
          });
        });
      };
  };

  return LabTestFormHelper;
});
