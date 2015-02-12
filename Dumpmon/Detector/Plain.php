<?php

namespace Dumpmon\Detector;

class Plain extends Detector
{
    public function analyze()
    {
        $score  = $this->detectEmailPwd();
        $score += $this->detectPwdStandalone();
        $score += $this->detectUsernamePwd() * 0.66;

        $this->score = $score;
    }

    /**
     * Detects lists of email:password(:username)?
     */
    protected function detectEmailPwd()
    {
        $emailPwd = preg_match_all("/^[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?[:|\||,|".'\t'."].*?[:".'\n'."]/im", $this->data);

        return $emailPwd / $this->lines;
    }

    /**
     * Detects password written as standalone
     * Password      : foobar
     * pass=foobar
     */
    protected function detectPwdStandalone()
    {
        $pwd = preg_match_all('/pass(?:word)?\s*?[:|=].\w+/im', $this->data);

        return $pwd / $this->lines;
    }

    /**
     * Detects lists of username:password
     * Its score is lowered since there could be a lot of false positive
     *
     */
    protected function detectUsernamePwd()
    {
        $pwd = preg_match_all('/^.{3,20}:.*?$/im', $this->data);

        return $pwd / $this->lines;
    }
}
