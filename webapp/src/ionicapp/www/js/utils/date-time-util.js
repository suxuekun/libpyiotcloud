
angular.module('dateTimeUtil', [])

.service('DateTimeUtil', [function(){

    var ret = {
        convertTimestampToDate: (timestamp) => {
          return new Date(Number(timestamp) * 1000)
        },
        getCurrentTimestamp: () => {
          return Math.floor(new Date().getTime() / 1000);
        },

        getPreviousTimestamp: (currentTime, minutes) => {
          return currentTime.setMinutes(currentTime.getMinutes() - minutes) / 1000
        }
    };

    return ret;
}]);
