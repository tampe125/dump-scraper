<?php

namespace Dumpmon\Extractor;

class Plain extends Extractor
{
    protected $emailRegex = "[a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}";

    public function analyze()
    {
        $data  = $this->extractUsernamePwd()."\n";
        $data .= $this->extractUrlWithPwd()."\n";
        $data .= $this->extractEmailPwd();

        $this->extracted = $data;
    }

    protected function extractEmailPwd()
    {
        preg_match_all('/^"?'.$this->emailRegex."\s?[\/|;|:|\||,|".'\t'."](.*?)[:".'\n'."]/im", $this->data, $matches);

        if(isset($matches[1]))
        {
            return implode("\n", $matches[1]);
        }

        return '';
    }

    /**
     * Detects lists of username:password
     */
    protected function extractUsernamePwd()
    {
        preg_match_all('/^[a-z0-9\-]{5,15}:(.*?)$/im', $this->data, $matches);

        if(isset($matches[1]))
        {
            return implode("\n", $matches[1]);
        }

        return '';
    }

    protected function extractUrlWithPwd()
    {
        preg_match_all('/[ht|f]tp[s]*:\/\/\w+\:(.*)\@\w*\.\w*/', $this->data, $matches);

        if(isset($matches[1]))
        {
            return implode("\n", $matches[1]);
        }

        return '';
    }
}