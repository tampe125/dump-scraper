<?php

namespace Dumpmon\Detector;

class Plain extends Detector
{
    protected $emailRegex = "[a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}";

    public function analyze($results)
    {
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
        $emailPwd = preg_match_all('/^"?'.$this->emailRegex."\s?[\/|;|:|\||,|".'\t'."].*?[:".'\n'."]/im", $this->data);

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
