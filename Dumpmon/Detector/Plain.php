<?php
/**
 * @package     Dumpmon Scraper
 * @copyright   2015 Davide Tampellini - FabbricaBinaria
 * @license     GNU GPL version 3 or later
 */

namespace Dumpmon\Detector;

class Plain extends Detector
{
    protected $emailRegex = '[a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}';

    public function analyze($results)
    {
        // If the Trash Detector has an high value, don't process the file, otherwise we could end up with a false positive
        // Sadly some list of emails only could be very hard to separate from email - pwd files
        if($results['trash'] >= 0.95)
        {
            $this->score = 0;

            return;
        }

        $score  = $this->detectEmailPwd();
        $score += $this->detectPwdStandalone();
        $score += $this->detectUsernamePwd() * 0.75;
        $score += $this->detectPwdEmails();

        $this->score = $score;
    }

    /**
     * Detects lists of email:password(:username)?
     */
    protected function detectEmailPwd()
    {
        $emailPwd = preg_match_all('/^[\s"]?'.$this->emailRegex.'\s?[\/|;|:|\||,|\t].*?[:\n]/im', $this->data);

        return $emailPwd / $this->lines;
    }

    /**
     * Detects password written as standalone
     * Password      : foobar
     * pass=foobar
     */
    protected function detectPwdStandalone()
    {
        $pwd = preg_match_all('/pass(?:word)?\s*?[:|=].*?$/im', $this->data);

        return $pwd / $this->lines;
    }

    /**
     * Detects lists of username:password
     */
    protected function detectUsernamePwd()
    {
        $pwd = preg_match_all('/^[a-z0-9]{5,15}:.{1,10}$/im', $this->data);

        return $pwd / $this->lines;
    }

    private function detectPwdEmails()
    {
        $score = preg_match_all("/.{4,15}[\s|\/|;|:|\||,|".'\t'."]".$this->emailRegex."\s*?$/im", $this->data);

        return $score / $this->lines;
    }
}
