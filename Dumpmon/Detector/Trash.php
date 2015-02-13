<?php

namespace Dumpmon\Detector;

class Trash extends Detector
{
    public function analyze()
    {
        // Single lines pastebin are always trash
        if($this->lines < 3)
        {
            $this->score = 3;
        }
        else
        {
            $score  = $this->detectEmailsOnly();
            $score += $this->longLines();
            $score += $this->privateKeys();
            $score += $this->detectDebug() * 1.2;
            $score += $this->detectIP() * 1.5;
            $score += $this->detectTimeStamps();
            $score += $this->detectHtml();

            $this->score = $score;
        }
    }

    /**
     * Detect full list of email addresses only, useless for us
     */
    protected function detectEmailsOnly()
    {
        $emails = preg_match_all("/^[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/im", $this->data);

        return $emails / $this->lines;
    }

    /**
     * Files with debug info
     *
     * @return float
     */
    protected function detectDebug()
    {
        $score   = preg_match_all('/0\x[a-f0-9]{8}/i', $this->data);
        $score  += substr_count($this->data, '#EXTINF');
        $score  += substr_count(strtolower($this->data), 'debug');
        $score  += substr_count(strtolower($this->data), '[trace]');
        $score  += substr_count(strtolower($this->data), 'session');
        $score  += substr_count(strtolower($this->data), 'class=');
        $score  += substr_count(strtolower($this->data), 'thread');
        $score  += substr_count(strtolower($this->data), 'uuid');

        return $score / $this->lines;
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

        // Do I have a table dump? If so I have to lower the score of the timestamps, since most likely it's the creation time
        $insert = substr_count($this->data, 'INSERT INTO');
        $mysql  = preg_match_all('/\+.*?\+/m', $this->data);

        // Do I have lines starting with a number? Maybe it's a table dump without any MySQL markup
        $digits = preg_match_all('/^\d{1,4}/m', $this->data) / $this->lines;

        if($insert > 3 || $mysql > 5 || $digits > 0.25)
        {
            $multiplier = 0.01;
        }

        // Mysql dates - 2015-11-02
        $dates  = preg_match_all('/(19|20)\d\d[\-\/.](0[1-9]|1[012])[\-\/.](0[1-9]|[12][0-9]|3[01])/', $this->data) * $multiplier;
        $score  = $dates / $this->lines;

        // English dates - 11-25-2015
        $dates  = preg_match_all('/(0[1-9]|1[012])[\-\/.](0[1-9]|[12][0-9]|3[01])[\-\/.](19|20)\d\d/', $this->data) * $multiplier;
        $score += $dates / $this->lines;

        // Search for the time only if the previous regex didn't match anything. Otherwise I'll count timestamps YYYY-mm-dd HH:ii:ss twice
        if($score < 0.01)
        {
            $time   = preg_match_all('/(?:2[0-3]|[01][0-9]):[0-5][0-9](?:\:[0-5][0-9])?/', $this->data) * $multiplier;
            $score += $time / $this->lines;
        }
        return $score;
    }

    /**
     * HTML tags in the file, most likely garbage
     *
     * @return float
     */
    protected function detectHtml()
    {
        $html = preg_match_all('/<\/?(?:html|div|p|div|script|link|span|u|ul|li|ol|a)+\s*\/?>/i', $this->data) * 1.5;
        $urls = preg_match_all('/\b(?:(?:https?):\/\/|www\.)[-A-Z0-9+&@#\/%=~_|$?!:,.]*[A-Z0-9+&@#\/%=~_|$]/i', $this->data) * 0.5;

        return ($html + $urls) / $this->lines;
    }

    /**
     * Files with huge lines are debug info
     *
     * @return int
     */
    private function longLines()
    {
        // This is a special case: porn passwords usually have tons of keywords and long lines (4k+)
        // Let's manually add an exception for those files and hope for the best
        if(strpos($this->data, 'XXX Porn Passwords') !== false)
        {
            return 0;
        }

        $lines = explode("\n", $this->data);

        foreach($lines as $line)
        {
            if(strlen($line) > 1000)
            {
                return 3;
            }
        }

        return 0;
    }

    /**
     * RSA private keys
     *
     * @return int
     */
    private function privateKeys()
    {
        if(strpos($this->data, 'BEGIN RSA PRIVATE KEY') !== false)
        {
            return 3;
        }

        return 0;
    }
}