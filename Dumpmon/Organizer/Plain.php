<?php

namespace Dumpmon\Organizer;

class Plain extends Organizer
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
        $emailPwd = preg_match_all('/.*?@.*?\.[a-z]{2,5}[:|\|].*?[:\n]/i', $this->data);

        return $emailPwd / $this->lines;
    }

    /**
     * Detects password written as standalone
     * Password      : foobar
     * pass=foobar
     */
    protected function detectPwdStandalone()
    {
        $pwd = preg_match_all('/pass(?:word)?\s*?[:|=].\w+/i', $this->data);

        return $pwd / $this->lines;
    }

    /**
     * Detects lists of username:password
     * Its score is lowered since there could be a lot of false positive
     *
     */
    protected function detectUsernamePwd()
    {
        $pwd = preg_match_all('/^[a-z0-9]*?:.*?$/im', $this->data);

        return $pwd / $this->lines;
    }
}
