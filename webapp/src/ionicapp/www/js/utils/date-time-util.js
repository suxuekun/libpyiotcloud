
angular.module('dateTimeUtil', [])

.service('DateTimeUtil', [function(){

    var ret = {
        convertTimestampToDate: (timestamp) => {
          return new Date(Number(timestamp) * 1000)
        }
    };

    return ret;
}]);
