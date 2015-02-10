<?php

namespace Dumpmon\Organizer;

class Trash extends Organizer
{
    public function analyze()
    {
        $score  = $this->detectEmailsOnly();
        $score += $this->detectDebug() * 1.2;
        $score += $this->detectIP() * 1.5;
        $score += $this->detectTimeStamps();
        $score += $this->detectHtml();

        $this->score = $score;
    }

    /**
     * Detect full list of email addresses only, useless for us
     */
    protected function detectEmailsOnly()
    {
        $emails = preg_match_all('/^.*?@.*?\.[a-z]{2,5}$/i', $this->data);

        return $emails / $this->lines;
    }

    /**
     * Files with debug info
     *
     * @return float
     */
    protected function detectDebug()
    {
        $hex   = preg_match_all('/0\x[a-f0-9]{8}/i', $this->data);
        $debug = substr_count($this->data, '#EXTINF');

        return ($hex + $debug) / $this->lines;
    }

    /**
     * Files with IP most likely are access log files
     */
    protected function detectIP()
    {
        $ip = preg_match_all('/\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/', $this->data);

        return $ip / $this->lines;
    }

    /**
     * Files with a lot of timestamps most likely are log files
     *
     * @return float
     */
    protected function detectTimeStamps()
    {
        $multiplier = 1;

        // Do I have a table dump? If so I have to lower the score of the timestamps, since most likely
        // it's the creation time
        $insert = substr_count($this->data, 'INSERT INTO');
        $mysql  = preg_match_all('/\+.*?\+/', $this->data);

        if($insert > 3 || $mysql > 5)
        {
            $multiplier = 0.25;
        }

        $time  = preg_match_all('/(?:2[0-3]|[01][0-9]):[0-5][0-9]:[0-5][0-9]/', $this->data) * $multiplier;
        $score = $time / $this->lines;

        $dates  = preg_match_all('/(19|20)\d\d[\-\/.](0[1-9]|1[012])[\-\/.](0[1-9]|[12][0-9]|3[01])/', $this->data) * $multiplier;
        $score += $dates / $this->lines;

        return $score;
    }

    /**
     * HTML tags in the file, most likely garbage
     *
     * @return float
     */
    protected function detectHtml()
    {
        $html = preg_match_all('/<\/?(?:html|div|p|div|script|link|span|u|ul|li|ol|a)+|\s*\/?>/i', $this->data) * 1.5;
        $urls = preg_match_all('/\b(?:(?:https?):\/\/|www\.)[-A-Z0-9+&@#\/%=~_|$?!:,.]*[A-Z0-9+&@#\/%=~_|$]/i', $this->data);

        return ($html + $urls) / $this->lines;
    }
}