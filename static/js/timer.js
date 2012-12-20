/**
 * Created with PyCharm.
 * User: 4qwee
 * Date: 12/20/12
 * Time: 9:42 PM
 */

var startTimer = function($container, callback)
{
    $container.empty();

    var $div = $('<div>').addClass('progress progress-striped active');
    var $bar = $('<div>').addClass('bar');
    $div.append($bar);

    $container.append($div);

    var startValue = 0;
    var intervalId = setInterval(function()
    {
        $bar.css('width', ++startValue + '%');

        if (startValue == 100)
        {
            clearInterval(intervalId);
            if (callback != undefined)
                callback();
        }
    }, 100);
};